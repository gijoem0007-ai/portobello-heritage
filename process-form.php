<?php
// ============================================================
$to_email = "admin@portobelloheritagetrust.co.uk";
$subject_prefix = "PHT Membership Application";
// ============================================================

header('Content-Type: application/json');

function respond($success, $error = '') {
    echo json_encode(['success' => $success, 'error' => $error]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    respond(false, 'Invalid request method.');
}

// Honeypot check
if (!empty($_POST['website'])) {
    respond(true);
}

$name      = trim($_POST['name'] ?? '');
$address   = trim($_POST['address'] ?? '');
$postcode  = trim($_POST['postcode'] ?? '');
$phone     = trim($_POST['phone'] ?? '');
$email     = trim($_POST['email'] ?? '');
$skills    = trim($_POST['skills'] ?? '');
$agree     = isset($_POST['agree']) ? 'Yes' : 'No';
$signature = trim($_POST['signature'] ?? '');

if (empty($name) || empty($address) || empty($postcode) || empty($phone) || empty($email) || empty($signature)) {
    respond(false, 'Please fill in all required fields.');
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(false, 'Please enter a valid email address.');
}

if ($agree !== 'Yes') {
    respond(false, 'Please confirm you agree to your details being included in the membership directory.');
}

// Strip newlines from header-sensitive fields
$name  = str_replace(["\r", "\n"], '', $name);
$email = str_replace(["\r", "\n"], '', $email);

$subject = $subject_prefix . " - " . $name;

$body  = "New PHT Membership Application\n";
$body .= "================================\n\n";
$body .= "Name: $name\n";
$body .= "Address: $address\n";
$body .= "Post code: $postcode\n";
$body .= "Telephone: $phone\n";
$body .= "Email: $email\n\n";
$body .= "Skills/advice offered:\n$skills\n\n";
$body .= "Agrees to directory inclusion: $agree\n";
$body .= "Typed signature: $signature\n";
$body .= "Date submitted: " . date('d/m/Y H:i') . "\n";

$headers = "From: noreply@" . $_SERVER['HTTP_HOST'] . "\r\n";
$headers .= "Reply-To: $email\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

if (mail($to_email, $subject, $body, $headers)) {
    respond(true);
} else {
    respond(false, 'Could not send application. Please try again later.');
}
