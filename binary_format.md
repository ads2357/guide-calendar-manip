
    entry: 576 bytes
        int32 year
        int32 month
        int32 day
        int32 hour
        char[25] padding = /' '{25}/
        char[] content = /' '*(content)' '*/
        char[] end = "\x01\x00"

    diary:
        (entry /\x00{8}/)* entry \x00{6}
