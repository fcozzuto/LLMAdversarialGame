def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    self_role = observation.get("self_role", "pursuer")

    obstacles = set()
    for p in observation.get("obstacles", []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                nx, ny = sx + dx, sy + dy
                if free(nx, ny):
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def eval_move(m):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        dist2 = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        center2 = (cx - nx) * (cx - nx) + (cy - ny) * (cy - ny)

        # Small deterministic bias: prefer advancing along the dominant axis
        ax = 0 if ox == sx else (1 if ox > sx else -1)
        ay = 0 if oy == sy else (1 if oy > sy else -1)
        adv = (1 if dx == ax else 0) + (1 if dy == ay else 0) + (1 if dx == 0 and ax == 0 else 0) + (1 if dy == 0 and ay == 0 else 0)

        if self_role == "evader":
            # maximize distance; then keep away from center slightly to avoid predictable line-of-advance
            return (dist2, center2, adv)
        else:
            # minimize distance; then approach center to reduce zigzag escape lanes
            return (-dist2, -center2, adv)

    best = None
    best_val = None
    for m in moves:
        v = eval_move(m)
        if best is None or v > best_val or (v == best_val and m < best):
            best = m
            best_val = v
    return [int(best[0]), int(best[1])]