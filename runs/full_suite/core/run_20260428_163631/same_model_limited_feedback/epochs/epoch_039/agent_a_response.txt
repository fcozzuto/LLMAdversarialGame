def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        resources = []
    best = None
    best_score = None

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            dres = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dres = 0
        dopp = manh(nx, ny, ox, oy)
        # Prefer approaching resources while staying away from opponent to contest less directly
        score = (-2.2 * dres) + (0.9 * dopp)
        # If opponent is very close, strongly avoid moving nearer
        cur_dopp = manh(x, y, ox, oy)
        if cur_dopp <= 3:
            score += 2.0 * (dopp - cur_dopp)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]