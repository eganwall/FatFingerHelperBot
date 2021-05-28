class LogUtilityConstants:
    error_loglevel = "ERROR"
    warn_loglevel = "WARN"
    info_loglevel = "INFO"

class LogUtility:
    def log_message(self, loglevel, log_msg):
        loglevel_key = "LOGLEVEL={}".format(loglevel)
        log_msg_key = "LOGMSG=[{}]".format(log_msg)

        log_string = "{} {}".format(loglevel_key, log_msg_key)

        print(log_string)

    def log_info_message(self, log_msg):
        self.log_message(LogUtilityConstants.info_loglevel, log_msg)

    def log_warn_message(self, log_msg):
        self.log_message(LogUtilityConstants.warn_loglevel, log_msg)

    def log_error_message(self, log_msg):
        self.log_message(LogUtilityConstants.error_loglevel, log_msg)