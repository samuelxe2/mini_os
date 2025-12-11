#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>

namespace py = pybind11;

struct PyBlock {
    int start;
    int size;
    int pid;
    bool locked;
};

py::list merge_buddies(py::list py_blocks) {
    std::vector<PyBlock> blocks;
    blocks.reserve(py_blocks.size());

    for (auto item : py_blocks) {
        auto t = item.cast<py::tuple>();
        PyBlock b;
        b.start = t[0].cast<int>();
        b.size = t[1].cast<int>();
        b.pid = t[2].cast<int>();
        b.locked = t[3].cast<bool>();
        blocks.push_back(b);
    }

    std::sort(blocks.begin(), blocks.end(), [](const PyBlock& a, const PyBlock& b) {
        return a.start < b.start;
    });

    while (true) {
        bool merged = false;
        std::size_t i = 0;
        while (i + 1 < blocks.size()) {
            const PyBlock& b1 = blocks[i];
            const PyBlock& b2 = blocks[i + 1];

            bool free1 = (b1.pid == -1) && (!b1.locked);
            bool free2 = (b2.pid == -1) && (!b2.locked);

            if (free1 && free2 && b1.size == b2.size && b2.start == (b1.start ^ b1.size)) {
                PyBlock nb;
                nb.start = b1.start;
                nb.size = b1.size * 2;
                nb.pid = -1;
                nb.locked = false;
                blocks.erase(blocks.begin() + i, blocks.begin() + i + 2);
                blocks.insert(blocks.begin() + i, nb);
                merged = true;
            } else {
                ++i;
            }
        }
        if (!merged) break;
    }

    py::list out;
    for (const auto& b : blocks) {
        out.append(py::make_tuple(b.start, b.size, b.pid, b.locked));
    }
    return out;
}

PYBIND11_MODULE(mini_os_cpp, m) {
    m.def("merge_buddies", &merge_buddies);
}
