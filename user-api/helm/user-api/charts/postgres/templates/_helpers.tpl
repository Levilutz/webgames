{{- define "postgres.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "postgres.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc (int (sub 63 10)) | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "postgres.fullname-migrate" -}}
{{- printf "%s-migrate" (include "postgres.fullname" .) }}
{{- end }}

{{- define "postgres.tag-migrate" -}}
{{- if and (not .Values.global.tagBaseOverride) (not .Values.migrate.image.tag) (not .Values.migrate.image.tagBase) }}
{{- fail "Image for migrate requires at least some tag set" }}
{{- end }}
{{- if .Values.migrate.image.tag }}
{{- .Values.migrate.image.tag }}
{{- else }}
{{- printf "%s-%s" (default .Values.migrate.image.tagBase .Values.global.tagBaseOverride) .Values.migrate.image.tagContainer }}
{{- end }}
{{- end }}

{{- define "postgres.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "postgres.selectorLabels" -}}
app.kubernetes.io/name: {{ include "postgres.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "postgres.labels" -}}
helm.sh/chart: {{ include "postgres.chart" . }}
{{ include "postgres.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "postgres.dnsname" -}}
{{- printf "%s.%s.svc.cluster.local" (include "postgres.fullname" .) .Release.Namespace }}
{{- end }}
