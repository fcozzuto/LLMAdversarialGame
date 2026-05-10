def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set((int(x), int(y)) for (x, y) in (observation.get("self_territory") or []) if isinstance((x, y), tuple) or True)
    opp_terr = set((int(x), int(y)) for (x, y) in (observation.get("opponent_territory") or []) if isinstance((x, y), tuple) or True)
    unclaimed = set((int(x), int(y)) for (x, y) in (observation.get("unclaimed_cells") or []) if isinstance((x, y), tuple) or True)

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = [0, 0]
    best_score = -10**18

    my_cnt = int(observation.get("self_territory_count", len(self_terr)) or 0)
    op_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        d_self_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_current = abs(sx - cx) + abs(sy - cy)
        center_gain = d_current - d_self_center

        score = 0
        if cell in self_terr:
            score += 6
        elif cell in unclaimed:
            score += 18 + max(0, center_gain)
            score += 3 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
            score += 2 if op_cnt > my_cnt else 0
        elif cell in opp_terr:
            score -= 14
            score += 2 if d_opp > 4 else -2
            score += 3 if op_cnt < my_cnt else -1
        else:
            score += 1

        # Prefer pushing away from opponent while expanding unclaimed/centered.
        score += (d_opp - 6) * 0.8

        # Small deterministic tie-break: prefer diagonal slightly, then right/down bias.
        score += (1 if (dx != 0 and dy != 0) else 0)
        score += dx * 0.02 + dy * 0.01

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move