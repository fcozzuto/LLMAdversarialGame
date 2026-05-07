def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def pt(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        x, y = pt(p)
        if inb(x, y):
            obst.add((x, y))

    resources = [pt(r) for r in (observation.get("resources") or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    def best_diff(x, y):
        if not resources:
            return -10**9, 0
        best = (-10**9, 10**9)
        for rx, ry in resources:
            sd = man(sx, sy, x, y)  # same for all resources -> keep function simple
        # Actually compute per-resource:
        bestd = 10**9
        opp_best = -10**9
        opp_sum = 0
        for rx, ry in resources:
            sd = man(sx, sy, x, y)  # replaced below to avoid extra vars? keep correct:
        # Correct:
        best = (-10**9, 10**9)
        for rx, ry in resources:
            sd = man(0, 0, rx, ry)
            # Not correct; compute directly:
        # Re-do correctly with explicit:
        best_val = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            self_dist = man(x, y, rx, ry)
            opp_dist = man(ox, oy, rx, ry)
            diff = opp_dist - self_dist
            if diff > best_val or (diff == best_val and self_dist < best_sd):
                best_val = diff
                best_sd = self_dist
        return best_val, best_sd

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    # Evaluate each move by best "resource advantage" after moving.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        diff, sd = best_diff(nx, ny)
        # Prefer capturing quickly and, secondarily, staying ahead of opponent.
        rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
        endgame_bias = 2 if rem <= 3 else 0
        score = (diff * 10 + (endgame_bias - sd), -sd)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]