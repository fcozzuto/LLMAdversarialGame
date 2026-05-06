def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None  # (score, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            sum_pos = 0
            sum_our = 0
            cap = 0
            for rx, ry in resources:
                od = man(ox, oy, rx, ry)
                ud = man(nx, ny, rx, ry)
                if ud == 0:
                    cap += 1
                dlt = od - ud
                if dlt > 0:
                    sum_pos += dlt
                sum_our += ud

            # Prefer captures/denial, then closer overall, lightly avoid drifting from opponent.
            score = 200 * cap + 35 * sum_pos - 2.5 * sum_our - 0.1 * man(nx, ny, ox, oy)
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]