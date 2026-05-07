def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 1 if sx < tx else (-1 if sx > tx else 0)
        dy = 1 if sy < ty else (-1 if sy > ty else 0)
        return [dx, dy]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):  # engine would keep in place, mimic that
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_score = 0.0
        for rx, ry in resources:
            md = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # prefer resources I'm closer to; break ties toward nearer-to-me and away from opponent
            my_score += (2.0 * (od - md) - 0.08 * md)
            # small bonus if we are already on the resource
            if md == 0:
                my_score += 50.0

        # slight penalty for moving away from center to reduce oscillations
        cx, cy = w / 2.0, h / 2.0
        my_score -= 0.01 * abs((nx - cx)) + 0.01 * abs((ny - cy))

        if my_score > best_score:
            best_score = my_score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]