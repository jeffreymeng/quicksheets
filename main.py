from graphics.graphics import main
import sys

args = sys.argv
if len(args) > 1:
    main(args[1])
else:
    main()
