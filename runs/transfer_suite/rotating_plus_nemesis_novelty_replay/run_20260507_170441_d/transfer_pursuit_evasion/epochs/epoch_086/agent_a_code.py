def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: md(c[0], c[1], ox, oy))

    # deterministic tie-break: same score -> smallest (dx,dy) by this order
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_to_opp = md(nx, ny, ox, oy)
        toward_far = -md(nx, ny, far_corner[0], far_corner[1])
        toward_near = -md(nx, ny, near_corner[0], near_corner[1])

        if is_evader:
            # maximize separation; also drift toward far corner; discourage getting closer to near corner
            score = (dist_to_opp * 10) + (toward_far * 1.0) + (toward_near * -0.3)
        else:
            # minimize separation; also bias toward blocking by keeping near player's near corner direction
            # (works well vs corner-focused evasion: deny approach to player's far corner)
            score = (-dist_to_opp * 10) + (md(nx, ny, far_corner[0], far_corner[1]) * -0.6) + (toward_near * 0.1)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]