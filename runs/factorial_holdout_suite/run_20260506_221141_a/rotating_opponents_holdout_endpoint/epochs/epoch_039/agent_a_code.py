def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_turns = int(observation.get("turns_remaining", 0) or 0)
    remaining = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    early = 1 if my_turns > 20 else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    cur_best_race = min(cheb(sx, sy, rx, ry) for rx, ry in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        my_d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        # Race/lead heuristic: prefer resources where we are closer than opponent.
        lead = -10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            margin = d2 - d1  # positive means we are closer
            if d1 == 0:
                margin += 6 + early * 2
            # Slightly avoid resources too far when time is low
            tpen = 0
            if my_turns < 15 and d1 > cur_best_race:
                tpen = 2
            v = margin * 3 + (d2 - d1) + (-d1) * 0.1 - tpen
            if v > lead:
                lead = v

        # Prevent dithering: penalize worsening closest distance unless capturing.
        worsen = 0
        if my_d > cur_best_race and my_d != 0:
            worsen = 2

        # Encourage progressing when many resources remain: greedy coverage.
        cover = (cur_best_race - my_d) * (2 if remaining > 6 else 1)

        val = lead + cover - worsen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]