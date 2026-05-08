def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    def valid(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def eval_pos(px, py):
        best = -10**9
        for rx, ry in resources:
            ds = man(px, py, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are strictly closer (intercept/steal), otherwise create pressure by maximizing advantage
            adv = do - ds
            if ds == 0:
                adv += 1000
            # Encourage not-too-far moves to keep tempo
            tempo = -ds
            # Mild blocking: if opponent is much closer, avoid unless we can beat them quickly next
            risk = 0
            if do < ds and ds <= do + 1:
                risk = -5
            sc = adv * 20 + tempo + risk
            if sc > best:
                best = sc
        return best

    best_move = (0, 0)
    best_score = -10**9
    # Deterministic tie-break: prefer (0,0), then smallest dx, then smallest dy in lexicographic order
    ordered = sorted(moves, key=lambda m: (0 if m == (0, 0) else 1, m[0], m[1]))
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        sc = eval_pos(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]