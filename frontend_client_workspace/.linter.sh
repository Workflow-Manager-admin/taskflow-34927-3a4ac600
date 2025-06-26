#!/bin/bash
cd /home/kavia/workspace/code-generation/taskflow-34927-3a4ac600/frontend_client_workspace/frontend_client
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

