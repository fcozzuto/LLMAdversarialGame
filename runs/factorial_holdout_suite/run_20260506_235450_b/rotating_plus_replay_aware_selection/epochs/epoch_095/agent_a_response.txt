def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Small preference for moving away from opponent when no clear advantage.
    best_move = legal[0]
    best_val = -10**9

    # Deterministic ordering of resources helps tie-breaking.
    res_sorted = sorted((int(r[0]), int(r[1])) for r in resources)

    for dx, dy, nx, ny in legal:
        # If move hits an occupied resource now, heavily prioritize.
        on_resource = 0
        best_gain = -10**9
        self_to_opp_now = md(nx, ny, ox, oy)
        for rx, ry in res_sorted:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Higher when we arrive earlier; penalize equal/later.
            gain = (od - sd)
            if sd == 0:
                gain += 100
            elif sd == 1:
                gain += 8
            elif sd == 2:
                gain += 3
            # Strong deterrence if opponent can beat us.
            if od <= sd:
                gain -= (6 - max(0, od - sd))  # keep bounded
            # Encourage taking nearer resources if ties.
            gain -= 0.1 * sd
            if gain > best_gain:
                best_gain = gain
                on_resource = 1 if (sd == 0) else on_resource
        # Prefer reducing opponent distance while improving best_gain.
        val = best_gain * 10 + (self_to_opp_now * -0.02)
        if on_resource:
            val += 50
        if val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]