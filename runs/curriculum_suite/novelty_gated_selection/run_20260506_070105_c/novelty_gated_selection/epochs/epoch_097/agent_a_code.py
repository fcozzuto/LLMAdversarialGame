def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    def manh(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    opp_penalty = 4
    my_bonus = 6
    speed = 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx * speed, sy + dy * speed
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        val = 0
        closest_target = None
        best_gain = -10**18
        for rx, ry in resources:
            d_me = manh(nx, ny, rx, ry)
            d_op = manh(ox, oy, rx, ry)
            # Prefer getting closer than opponent to a resource; reward immediate grabs.
            gain = (d_op - d_me) - opp_penalty * (d_me == 0)
            if d_me == 0:
                gain += my_bonus
            if gain > best_gain:
                best_gain = gain
                closest_target = (rx, ry)

        # Break ties with proximity to the selected target and avoid standing still.
        if closest_target is not None:
            tx, ty = closest_target
            val = best_gain * 10 - manh(nx, ny, tx, ty)
        if dx == 0 and dy == 0:
            val -= 1

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move