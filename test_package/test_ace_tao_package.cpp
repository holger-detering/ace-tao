#include <ace/Date_Time.h>

#include <iostream>

int main() {
    ACE_Date_Time now{};

    std::cout << "Now is the year " << now.year() << ".\n";
}
