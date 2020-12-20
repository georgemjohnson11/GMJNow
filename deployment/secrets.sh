#https://stackoverflow.com/questions/49654457/how-to-auto-deploy-docker-containers-from-amazon-ecr-to-kubernetes-using-jenkins/50502171#50502171


TOKEN=`aws ecr --region=$REGION get-authorization-token --output text --query authorizationData[].authorizationToken | base64 -d | cut -d: -f2`
echo $TOKEN
kubectl delete secret --ignore-not-found $SECRET_NAME
kubectl create secret docker-registry $SECRET_NAME \
 --docker-server=https://${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com \
 --docker-username=AWS \
 --docker-password="${TOKEN}" \
 --docker-email="${EMAIL}"