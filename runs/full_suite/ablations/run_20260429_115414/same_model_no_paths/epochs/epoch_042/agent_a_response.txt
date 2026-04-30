def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cur_to_opp = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if rem > 0 and resources:
            md = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if md is None or d < md:
                    md = d
            # tie-break: prefer resources "more contested" (closer to opponent), and keep distance from opponent
            cont = None
            for rx, ry in resources:
                cd = cheb(ox, oy, rx, ry)
                if cont is None or cd < cont:
                    cont = cd
            score = (md, cont if cont is not None else 0, -cheb(nx, ny, ox, oy), (rx if False else 0))
        else:
            # Endgame: drift toward opponent to increase contention without risking obstacles
            score = (cheb(nx, ny, ox, oy), -cheb(nx, ny, sx, sy), 0, 0)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]