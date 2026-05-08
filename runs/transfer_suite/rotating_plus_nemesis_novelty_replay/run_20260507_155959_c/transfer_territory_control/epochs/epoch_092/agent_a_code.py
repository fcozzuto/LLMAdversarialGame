def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = [(int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    def adj_to(x, y, s):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in s:
                return True
        return False

    def score_cell(x, y):
        if not free(x, y): 
            return -10**9
        if (x, y) in self_t:
            return -10**6
        center_dist = abs(x - cx) + abs(y - cy)
        my_dist = abs(x - sx) + abs(y - sy)
        to_opp = 1 if adj_to(x, y, opp_t) else 0
        to_self = 1 if adj_to(x, y, self_t) else 0
        flip_bias = 8 if (x, y) in opp_t else 0
        return (-center_dist) * 2.0 - my_dist + to_opp * 5 + to_self * 1 + flip_bias

    # If unclaimed exists, contest near center; otherwise move toward opponent to enable flips.
    candidates = []
    for (x, y) in unclaimed:
        if (x, y) not in self_t:
            candidates.append((score_cell(x, y), x, y))
    if candidates:
        candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
        tx, ty = candidates[0][1], candidates[0][2]
    else:
        tx, ty = ox, oy  # push into opponent influence when no unclaimed targets

    best = (0, 0, 0)  # (heur, dx, dy)
    for dx, dy in [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny) and (nx, ny) not in self_t and (nx, ny) not in opp_t:
            continue
        # Encourage stepping into opponent territory (flip on entry) and toward target.
        flip = 20 if (nx, ny) in opp_t else 0
        step_center = abs(nx - cx) + abs(ny - cy)
        toward = - (abs(nx - tx) + abs(ny - ty))
        own_adj = 1 if adj_to(nx, ny, self_t) else 0
        h = flip + toward + (-step_center) * 0.5 + own_adj
        if (h, dx, dy) > best:
            best = (h, dx, dy)

    return [int(best[1]), int(best[2])]