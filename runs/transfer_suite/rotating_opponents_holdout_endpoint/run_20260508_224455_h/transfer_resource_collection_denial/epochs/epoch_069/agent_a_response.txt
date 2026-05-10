def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obs)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target resource with strongest "can arrive first" advantage
    best = None
    for rx0, ry0 in resources:
        rx, ry = int(rx0), int(ry0)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer resources that are also "behind" relative to opponent vertically to reduce contention
        row_bias = 0
        if oy < sy:
            row_bias = -(ry - sy)
        elif oy > sy:
            row_bias = (ry - sy)
        advantage = (od - sd) * 20 - sd + row_bias
        if best is None or advantage > best[0]:
            best = (advantage, rx, ry)
    _, tx, ty = best

    # Evaluate possible moves with obstacle check and 1-step look
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = (-(10**9), 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd1 = cheb(nx, ny, tx, ty)
        # keep aiming to beat opponent if they go for same target
        od_same = cheb(ox, oy, tx, ty)
        # small deterministic tie-break toward reducing both axes
        axis = abs(nx - tx) + abs(ny - ty)
        score = (od_same - sd1) * 30 - sd1 - axis * 0.01
        if score > best_move[0]:
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]