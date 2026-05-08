def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def has_side_neighbor(cellset, x, y):
        return ((x - 1, y) in cellset) or ((x + 1, y) in cellset) or ((x, y - 1) in cellset) or ((x, y + 1) in cellset)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_cells:
            score += 6
        elif (nx, ny) in unclaimed:
            score += 45
            if has_side_neighbor(self_cells, nx, ny):
                score += 20
            if has_side_neighbor(opp_cells, nx, ny):
                score -= 10
        elif (nx, ny) in opp_cells:
            score += 28  # flipping likely helps
            score -= 2 * (has_side_neighbor(opp_cells, nx, ny) and 1 or 0)

        score += 2 * (md(ox, oy, sx, sy) - md(ox, oy, nx, ny))  # prefer moving away from opponent
        score += -1 * md(ox, oy, nx, ny) * 0  # keep deterministic structure

        # subtle determinism: prefer reducing distance to nearest unclaimed that touches our territory
        best_touch = 999
        for ux, uy in unclaimed:
            if has_side_neighbor(self_cells, ux, uy):
                d = md(nx, ny, ux, uy)
                if d < best_touch:
                    best_touch = d
        if best_touch != 999:
            score += -3 * best_touch

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]