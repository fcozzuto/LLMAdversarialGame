def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("pos")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x")
                y = r.get("y")
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    # If no resources, head toward center to avoid dead-end cornering.
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Choose resource I can secure: minimize (my_dist - opp_dist*0.9) with obstacle-aware tie-break.
        best = None
        bestv = 10**9
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer closer-to-me; strongly avoid targets opponent likely to reach first.
            v = md - 0.9 * od
            # Mild bias toward reachable directions (stay off obstacles) without full search.
            # Tie-break: prefer resource that is nearer to my current best move "front".
            if v < bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    # Move one step toward chosen target, but avoid getting into cells adjacent to many obstacles.
    moves = []
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Evaluate: closer to target, and avoid "trap" by obstacle neighborhood
        dist_to = cheb(nx, ny, tx, ty)
        trap = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            if blocked(nx + ax, ny + ay):
                trap += 1
        # Also avoid stepping too directly onto opponent when distances are similar.
        nopp = cheb(nx, ny, ox, oy)
        mynow = cheb(sx, sy, ox, oy)
        opp_pen = 0 if nopp >= mynow else (mynow - nopp) * 0.25
        score = dist_to + trap * 0.06 + opp_pen
        moves.append((score, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]