def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit", "pursuer"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer progress even if avoiding obstacles; if blocked, the engine keeps us in place.
    def eval_next(nx, ny):
        if (nx, ny) in obstacles:
            nx, ny = sx, sy  # simulate engine behavior
            blocked = 1
        else:
            blocked = 0

        d_opp = abs(nx - ox) + abs(ny - oy)
        # If pursuer: minimize distance; if evader: maximize distance (score shaped by inverse objective)
        primary = -d_opp if is_pursuer else d_opp

        # Extra shaping: avoid moving into/adjacent to obstacles to reduce chances of "staying put"
        adj_pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in obstacles:
                    adj_pen += 1
        # Resources: if any, pursuer goes for nearest; evader goes for farthest.
        best_res = None
        for r in observation.get("resources") or []:
            if r and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if 0 <= rx < w and 0 <= ry < h:
                    dist = abs(nx - rx) + abs(ny - ry)
                    if best_res is None or (dist < best_res):
                        best_res = dist
        res_term = 0
        if best_res is not None:
            res_term = (-best_res if is_pursuer else best_res)

        return primary + (0.25 * res_term) - (3.0 * blocked) - (0.8 * adj_pen)

    # Deterministic tie-breaking: fixed move order + exact score
    best_m = moves[4]
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        v = eval_next(nx, ny)
        if best_v is None or v > best_v:
            best_v = v
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]