def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b, c, d):
        ad = a - c
        if ad < 0: ad = -ad
        bd = b - d
        if bd < 0: bd = -bd
        return ad + bd

    def opp_line_penalty(nx, ny):
        # discourage moving toward opponent corner cluster when advantages are low
        return 0.02 * dist(nx, ny, ox, oy)

    if not resources:
        best_move = None
        best_val = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = dist(nx, ny, ox, oy) - 0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_move = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Choose the resource that gives the best immediate advantage after this move
        best_adv = -10**18
        best_self_d = 10**9
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = (od - sd)  # positive means we're closer than opponent
            # tie-break: prefer shorter self distance
            if adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv = adv
                best_self_d = sd

        # Primary: maximize advantage; Secondary: commit to getting there; Tertiary: keep distance from opponent
        val = best_adv * 3.0 - 0.15 * best_self_d - opp_line_penalty(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]