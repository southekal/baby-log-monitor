import random
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

skill_name = "Baby Data"
help_text = ("You can say baby slept at 2pm or "
"had a diaper change at 2:30pm "
"or that the last feed was at 11am")

sleep_slot_key = "SLEEP"
diaper_slot_key = "DIAPER"
feed_slot_key = "FEED"
baby_name_slot_key = "BABY"
sleep_slot = "Sleep"
diaper_slot = "Diaper"
feed_slot = "Feed"
baby_name_slot = "Baby"


# sb = SkillBuilder()
sb = StandardSkillBuilder(table_name="alexa-baby-data", auto_create_table=True)

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    # Handler for Skill Launch
    
    attr = handler_input.attributes_manager.persistent_attributes
    handler_input.attributes_manager.session_attributes = attr

    if not attr:
        missing_name_text = "What is the name of your baby? Say my baby's name is Jane"      
        handler_input.response_builder.speak(missing_name_text).ask(missing_name_text)
        return handler_input.response_builder.response

    baby_name = attr[baby_name_slot_key]
    display_text = "Hi {}! welcome back!... {}".format(baby_name, help_text) 
    handler_input.response_builder.speak(display_text).ask(display_text)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # Handler for Help Intent
    handler_input.response_builder.speak(help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name("AMAZON.CancelIntent")(input) or
        is_intent_name("AMAZON.StopIntent")(input))
def cancel_and_stop_intent_handler(handler_input):
    # Single handler for Cancel and Stop Intent
    speech_text = "Thank you and come again!"

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    # Handler for Session End
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("BabyNameIntent"))
def baby_name_handler(handler_input):

    slots = handler_input.request_envelope.request.intent.slots

    if baby_name_slot in slots and slots[baby_name_slot].value is not None:
        _name = slots[baby_name_slot].value
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr[baby_name_slot_key] = _name

        # save session in dynamodb
        handler_input.attributes_manager.persistent_attributes = session_attr
        handler_input.attributes_manager.save_persistent_attributes()

        speech = ("Hi baby {baby_name}! "
        "I now know your name!.. {help_text}".format(baby_name=_name, help_text=help_text))
        reprompt = ("Please tell me your "
        "baby's name by saying, my baby's name is")

        handler_input.response_builder.speak(speech).ask(reprompt)
    else:
        text = "Please tell me your "
        "baby's name by saying, my baby's name is"

        handler_input.response_builder.ask(text)
    
    return handler_input.response_builder.response


def answer_data_handler(handler_input, slot_key, keyword):
    attr = handler_input.attributes_manager.persistent_attributes
    handler_input.attributes_manager.session_attributes = attr
    session_data = handler_input.attributes_manager.session_attributes
    
    baby_name = session_data[baby_name_slot_key]
    
    rolling_text = [
        "Don't forget, Mommy loves you", 
        "And yes...Amma and accha loves you", 
        "Also your ajja and ajji say hi", 
        "And dad says you are a burrito and he will eat you up"
    ]

    if slot_key in session_data:
        data = session_data[slot_key]
        speech = ("{} {} last at {}. {}!".format(baby_name, keyword, data, random.choice(rolling_text)))

        #handler_input.response_builder.set_should_end_session(True)
    else:
        speech = "I don't think I know when {} {} last. ".format(baby_name, keyword) + help_text
        handler_input.response_builder.ask(help_text)

    handler_input.response_builder.speak(speech)
    return handler_input.response_builder.response
    

def set_data_handler(handler_input, slot_type, slot_type_key, keyword):
    session_data = handler_input.attributes_manager.session_attributes
    slots = handler_input.request_envelope.request.intent.slots
    baby_name = session_data[baby_name_slot_key]

    if slot_type in slots and slots[slot_type].value is not None:
        data = slots[slot_type].value
        handler_input.attributes_manager.session_attributes[
            slot_type_key] = data
        
        # save session in dynamodb
        handler_input.attributes_manager.persistent_attributes = handler_input.attributes_manager.session_attributes
        handler_input.attributes_manager.save_persistent_attributes()
        
        speech = ("Now I know that {baby_name}'s last {keyword} was at {data}. "
                  "You can ask me {baby_name}'s {keyword} time by saying, "
                  "when did {baby_name} {keyword} last ?".format(baby_name=baby_name, data=data, keyword=keyword))
        reprompt = ("You can ask me {baby_name}'s {keyword} time by saying, "
                    "when did she {keyword} last ?".format(baby_name=baby_name, keyword=keyword))
    else:
        speech = "I'm not sure when {baby_name} had her {keyword} last, please try again".format(baby_name=baby_name, keyword=keyword)
        reprompt = ("I'm not sure when {baby_name} had her {keyword} last.".format(baby_name=baby_name, keyword=keyword))

    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("WhatIsSleepTimeIntent"))
def sleep_time_handler(handler_input):

    return answer_data_handler(
        handler_input=handler_input, 
        slot_key=sleep_slot_key,
        keyword="slept")


@sb.request_handler(can_handle_func=is_intent_name("SleepIntent"))
def sleep_handler(handler_input):

    return set_data_handler(
        handler_input=handler_input, 
        slot_type=sleep_slot, 
        slot_type_key=sleep_slot_key, 
        keyword="sleep"
    )
    

@sb.request_handler(can_handle_func=is_intent_name("WhatIsFeedTimeIntent"))
def feed_time_handler(handler_input):

    return answer_data_handler(
        handler_input=handler_input, 
        slot_key=feed_slot_key,
        keyword="fed"
    )    


@sb.request_handler(can_handle_func=is_intent_name("FeedIntent"))
def feed_handler(handler_input):

    return set_data_handler(
        handler_input=handler_input, 
        slot_type=feed_slot, 
        slot_type_key=feed_slot_key, 
        keyword="feed"
    )


@sb.request_handler(can_handle_func=is_intent_name("WhatIsDiaperIntent"))
def diaper_time_handler(handler_input):
    
    return answer_data_handler(
        handler_input=handler_input, 
        slot_key=diaper_slot_key,
        keyword="changed her diaper"
    )    


@sb.request_handler(can_handle_func=is_intent_name("DiaperIntent"))
def diaper_handler(handler_input):
    
    return set_data_handler(
        handler_input=handler_input, 
        slot_type=diaper_slot, 
        slot_type_key=diaper_slot_key, 
        keyword="diaper change"
    )
    
   
@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    speech = ("The {} skill can't help you with that. ").format(skill_name)
    speech += help_text
    reprompt = help_text
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


@sb.global_response_interceptor()
def log_response(handler_input, response):
    # Log response from alexa service
    print("Alexa Response: {}\n".format(response))


@sb.global_request_interceptor()
def log_request(handler_input):
    # Log request to alexa service
    print("Alexa Request: {}\n".format(handler_input.request_envelope.request))


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # Catch all exception handler, log exception and
    # respond with custom message
    print("Encountered following exception: {}".format(exception))

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


# Handler to be provided in lambda console.
handler = sb.lambda_handler()