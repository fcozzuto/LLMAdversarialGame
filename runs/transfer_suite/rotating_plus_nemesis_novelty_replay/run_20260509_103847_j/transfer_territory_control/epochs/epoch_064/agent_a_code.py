def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = list(unT)
    if not candidates:
        for p in opT:
            candidates.append(p)
        if not candidates:
            return [0, 0]

    op_points = list(opT)[:64]
    un_points = candidates[:64]

    def mindist(pt_list, x, y):
        best = 10**9
        for px, py in pt_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best if pt_list else best

    scored = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            scored.append((-10**9, 10**9, 0, dx, dy))
            continue
        in_un = (nx, ny) in unT
        in_op = (nx, ny) in opT
        in_self = (nx, ny) in selfT

        val = 0
        if in_un:
            val += 4
        if in_op:
            val += 3  # flipping on entry, prioritize raids
        if in_self:
            val += 1

        # Favor frontier: move closer to unclaimed; also avoid getting dragged too deep into opponent
        d_un = mindist(un_points, nx, ny)
        d_op = mindist(op_points, nx, ny)
        val += (25 - d_un) * 0.2
        val += (d_op - 3) * 0.02  # slightly prefer staying a bit away unless raiding

        # Small preference for expanding (not oscillating) via deterministic tie-break on coordinates
        scored.append((val, d_un, -(dx * dx + dy * dy), dx, dy))

    scored.sort(reverse=True)
    _, _, _, dx, dy = scored[0]
    return [int(dx), int(dy)]