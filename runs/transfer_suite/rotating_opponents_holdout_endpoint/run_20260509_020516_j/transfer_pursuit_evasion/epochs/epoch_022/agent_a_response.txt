def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    pursuer = ("pursuer" in srole) or (("evader" in orole) and ("pursuer" not in srole))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # wall-running behavior: if opponent is on a wall, bias towards that wall alignment
    on_wall = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        mob = mobility(nx, ny)
        d = dist2(nx, ny, ox, oy)

        if pursuer:
            # minimize distance; slightly prefer safer/more mobile cells; if opponent on wall, prefer reducing the "wall coordinate" gap
            wall_align = 0
            if on_wall:
                if ox == 0 or ox == w - 1:
                    wall_align = abs(nx - ox)
                else:
                    wall_align = abs(ny - oy)
            val = d - 0.08 * mob + 0.02 * edge_dist(nx, ny) + 0.35 * wall_align
            better = (best_val is None) or (val < best_val)
        else:
            # maximize distance; avoid low mobility traps; prefer moving toward the farther side while staying mobile
            val = -d + 0.06 * mob + 0.02 * (edge_dist(nx, ny))
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]