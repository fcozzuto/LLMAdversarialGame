def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    capr = observation.get("capture_radius", 0)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]
    dirs.sort(key=lambda t: (t[0], t[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = observation.get("self_role", "")
    is_evader = role.lower() == "evader"

    def cheb(x, y):
        return max(abs(x - ox), abs(y - oy))

    def obstacle_penalty(x, y):
        p = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                nx, ny = x + tx, y + ty
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    p += 1
                elif (nx, ny) in obstacles:
                    p += 2
        return p

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d = cheb(nx, ny)
        base = -d if not is_evader else d

        # Strong preference if we can capture (capture_radius=0 implies exact position)
        if capr == 0 and nx == ox and ny == oy:
            base += 1000 if not is_evader else -1000

        # Encourage quicker approach/escape
        curr_d = cheb(sx, sy)
        delta = curr_d - d  # positive means closer
        shaped = base + (10 * delta if not is_evader else -10 * delta)

        # Avoid getting stuck near walls/obstacles
        score = shaped - obstacle_penalty(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]