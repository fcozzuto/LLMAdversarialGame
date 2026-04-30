def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_move = [0, 0]
    best_score = -10**18
    has_res = bool(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        oppd = md(nx, ny, ox, oy)
        if has_res:
            mind = 10**9
            for rx, ry in resources:
                d = md(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            # Prefer stepping onto/near resources; also keep some distance from opponent.
            score = (1000 - 50 * mind) + (oppd * 2)
        else:
            # No visible resources: drift away from opponent and toward center.
            cx, cy = w // 2, h // 2
            centd = md(nx, ny, cx, cy)
            score = (oppd * 3) - centd
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move