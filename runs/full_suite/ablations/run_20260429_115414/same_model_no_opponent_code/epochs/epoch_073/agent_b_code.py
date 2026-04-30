def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target():
        if not resources:
            return None
        best = None
        best_score = -10**18
        for tx, ty in resources:
            ds = manh(sx, sy, tx, ty)
            do = manh(ox, oy, tx, ty)
            # prefer resources we can reach sooner; small tie-break toward closer
            score = (do - ds) * 10_000 - ds
            if score > best_score:
                best_score = score
                best = (tx, ty)
        return best

    target = best_target()

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if target is None:
            # fallback: maximize distance from opponent while staying in-bounds
            val = manh(nx, ny, ox, oy)
        else:
            tx, ty = target
            # move toward target; also discourage letting opponent become closer
            ds2 = manh(nx, ny, tx, ty)
            do2 = manh(ox, oy, tx, ty)
            val = (do2 - ds2) * 10_000 - ds2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]