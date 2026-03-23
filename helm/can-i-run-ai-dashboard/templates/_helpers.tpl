{{- define "can-i-run-ai-dashboard.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "can-i-run-ai-dashboard.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "can-i-run-ai-dashboard.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "can-i-run-ai-dashboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "can-i-run-ai-dashboard.selectorLabels" -}}
app.kubernetes.io/name: {{ include "can-i-run-ai-dashboard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "can-i-run-ai-dashboard.gatewayName" -}}
{{- printf "%s-gateway" (include "can-i-run-ai-dashboard.fullname" .) -}}
{{- end -}}

{{- define "can-i-run-ai-dashboard.gatewayHost" -}}
{{- printf "*.%s" .Values.istio.baseDomain -}}
{{- end -}}

{{- define "can-i-run-ai-dashboard.virtualServiceName" -}}
{{- printf "%s-virtualservice" (include "can-i-run-ai-dashboard.fullname" .) -}}
{{- end -}}

{{- define "can-i-run-ai-dashboard.virtualServiceHost" -}}
{{- printf "%s.%s" .Values.istio.virtualService.subdomain .Values.istio.baseDomain -}}
{{- end -}}
