def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_score = -10**18
        for tx, ty in resources:
            md = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer resources I can reach no later; otherwise contest by choosing closest "gap"
            score = (od - md) * 1000 - md
            # Slight tie-break: bias toward resources on my side (lower x+y) deterministically
            score += -0.01 * (tx + ty)
            if score > best_score:
                best_score = score
                best = (tx, ty)

        tx, ty = best
        best_move = (0, 0)
        best_md = 10**9
        # If multiple moves tie, pick deterministically by move ordering and distance to opponent
        best_opd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            md = cheb(nx, ny, tx, ty)
            if md < best_md:
                best_md = md
                best_opd = cheb(nx, ny, ox, oy)
                best_move = (dx, dy)
            elif md == best_md:
                opd = cheb(nx, ny, ox, oy)
                if opd < best_opd:
                    best_opd = opd
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources left: drift to deny opponent by moving to a corner farthest from them
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]) - cheb(sx, sy, c[0], c[1]))
    tx, ty = target
    best_move = (0, 0)
    best_md = 10**9
    best_opd = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        md = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        if md < best_md or (md == best_md and opd > best_opd):
            best_md = md
            best_opd = opd
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]