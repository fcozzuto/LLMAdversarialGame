def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer races we can win; also avoid targets that look too close to opponent.
    bestT = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Primary: opponent further than us
        win_margin = do - ds
        # Secondary: prefer nearer targets once we have an advantage
        # Tertiary: bias toward higher y then x deterministically
        score = (win_margin, -ds, -ry, -rx)
        if bestT is None or score > bestT[0]:
            bestT = (score, rx, ry)
    _, tx, ty = bestT

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose move that improves our distance to target while worsening opponent's distance to same target.
    bestM = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my = md(nx, ny, tx, ty)
        opd = md(ox + 0, oy + 0, tx, ty)  # opponent assumed may change; baseline discourages giving up advantage
        # Use one-step "likely" opponent response: if we move closer, assume opponent can also choose similarly;
        # approximate by penalizing moves that reduce our lead too much.
        my_now = md(sx, sy, tx, ty)
        do_now = md(ox, oy, tx, ty)
        lead_now = do_now - my_now
        lead_new = do_now - my  # opponent position unchanged approximation
        score = (lead_new, -my, -abs((tx - nx) - (ty - ny)), dx, dy, -rx) if False else (lead_new, -my, -abs(tx - nx) - abs(ty - ny), dx, dy)
        if bestM is None or score > bestM[0]:
            bestM = (score, dx, dy)

    if bestM is None:
        return [0, 0]
    return [int(bestM[1]), int(bestM[2])]