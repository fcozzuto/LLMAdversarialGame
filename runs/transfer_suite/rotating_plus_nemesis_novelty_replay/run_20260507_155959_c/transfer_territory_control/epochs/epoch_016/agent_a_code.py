def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_terr = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]
    unclaimed_set = set(unclaimed)

    grid_unclaimed_sample = unclaimed[:24] if unclaimed else []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cell_state = 0
        if (nx, ny) in unclaimed_set:
            cell_state = 3
        elif (nx, ny) in self_terr:
            cell_state = 2
        elif (nx, ny) in opp_terr:
            cell_state = 1

        # nearest unclaimed distance from next position (sampled)
        best_ud = 10**9
        if grid_unclaimed_sample:
            for ux, uy in grid_unclaimed_sample:
                d = abs(nx - ux) + abs(ny - uy)
                if d < best_ud:
                    best_ud = d

        # if we are behind, prioritize closer unclaimed and direct pressure; else keep away slightly
        self_cnt = observation.get("self_territory_count", len(self_terr)) or 0
        opp_cnt = observation.get("opponent_territory_count", len(opp_terr)) or 0
        behind = 1 if self_cnt < opp_cnt else 0

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # Encourage pressure: being closer to opponent territory helps when behind, otherwise avoid
        pressure = (-dist_to_opp) if behind else dist_to_opp

        # Small bias toward diagonal/forward movement to avoid being stuck
        move_bias = 0
        if dx != 0 and dy != 0:
            move_bias = 0.15

        if cell_state == 0:
            cell_score = -5
        else:
            cell_score = 9 * cell_state

        unclaimed_term = -best_ud if best_ud < 10**9 else 0
        score = cell_score + (3.2 * unclaimed_term) + (0.8 * pressure) + move_bias

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]