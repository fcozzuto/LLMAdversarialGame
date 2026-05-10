def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_cost(nx, ny):
        if (nx, ny) in obstacles:
            return 10**9
        d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev capture proxy
        if is_pursuer:
            base = d
        else:
            base = -d  # maximize distance when evading

        # small deterministic shaping to reduce getting stuck near obstacles
        adj_block = 0
        for dx, dy in moves:
            xx, yy = nx + dx, ny + dy
            if inb(xx, yy) and (xx, yy) in obstacles:
                adj_block += 1
        base += adj_block * (0.01 if is_pursuer else -0.01)

        # deterministic tie-break: prefer diagonal when it changes both coordinates toward/away
        tieb = 0
        if (nx != sx) and (ny != sy):
            tieb -= 0.001 if is_pursuer else 0.001
        return base + tieb

    best_move = (0, 0)
    best_val = None
    # Deterministic preference order: try moves that align with pursuer/evader direction first
    order = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            order.append((10**8 + abs(dx) + abs(dy), (dx, dy)))
        else:
            alignx = (dx == 0) or ((ox - sx) == 0) or (dx * (ox - sx) > 0)
            aligny = (dy == 0) or ((oy - sy) == 0) or (dy * (oy - sy) > 0)
            # If evader, alignment is opposite direction
            if not is_pursuer:
                alignx = (dx == 0) or ((ox - sx) == 0) or (dx * (ox - sx) < 0)
                aligny = (dy == 0) or ((oy - sy) == 0) or (dy * (oy - sy) < 0)
            pref = (0 if (alignx and aligny) else (1 if (alignx or aligny) else 2))
            order.append((pref, (dx, dy)))
    order.sort(key=lambda z: z[0])

    for _, (dx, dy) in order:
        nx, ny = sx + dx, sy + dy
        v = step_cost(nx, ny)
        if best_val is None or v < best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]