def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        best_res = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; otherwise still head to reduce opp lead.
            adv = opp_d - my_d
            # Score: primary by advantage, secondary by keeping my distance small, tertiary by favoring near resources globally.
            res_score = (adv, -my_d, -(cheb(sx, sy, rx, ry)))
            if best_res is None or res_score > best_res:
                best_res = res_score
        if best_res is None:
            continue
        if best_score is None or best_res > best_score:
            best_score = best_res
            best_move = [dx, dy]

    return best_move