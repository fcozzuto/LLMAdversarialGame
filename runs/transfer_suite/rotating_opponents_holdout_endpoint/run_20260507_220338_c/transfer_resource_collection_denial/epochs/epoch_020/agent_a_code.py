def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    # Consider a small deterministic subset: nearest by our distance
    scored_res = []
    for rx, ry in resources:
        d = md(sx, sy, rx, ry)
        scored_res.append((d, rx, ry))
    scored_res.sort(key=lambda t: (t[0], t[1], t[2]))
    top = scored_res[: min(8, len(scored_res))]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        for d0, rx, ry in top:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            if sd == 0 and (nx, ny) == (rx, ry):
                score += 10**9

            # Relative advantage: larger means we are closer than opponent
            rel = od - sd
            # Encourage approaching resources; discourage letting opponent be closer
            score += rel * 50

            # Small preference for overall closeness to finish sooner
            score += (max(0, 20 - sd)) * 3

            # Extra push if we can beat opponent at this resource next
            if sd < od:
                score += 80
            elif sd == od:
                score -= 20

        # Deterministic tie-break: prefer lower dx, then lower dy, then lexicographic position
        tie = (score, -abs(dx) - abs(dy), -nx, -ny, dx, dy)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]