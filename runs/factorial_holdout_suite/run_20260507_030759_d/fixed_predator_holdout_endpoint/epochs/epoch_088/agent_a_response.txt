def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def res_priority(rx, ry):
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # Prefer resources opponent is farther from; then closer to self; then deterministic cell order.
        return (opp_d - self_d, -self_d, -rx, -ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose target greedily among resources, then select a move that best improves achievable priority.
    target = max(resources, key=lambda r: res_priority(r[0], r[1]))

    tx, ty = target
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate next-step advantage: if target cell reachable sooner, prioritize it; otherwise pick best remaining resource from next pos.
        # Deterministic, lightweight: use the same priority but from (nx, ny).
        best_next = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            pri = (od - sd, -sd, -rx, -ry)
            if best_next is None or pri > best_next[0]:
                best_next = (pri, rx, ry)
        pri = best_next[0] if best_next else (-10**9, 0, 0, 0)
        # Slightly prefer moving toward the greedy target to reduce wandering.
        toward = -md(nx, ny, tx, ty)
        pri2 = (pri, toward)
        if best is None or pri2 > best[0] or (pri2 == best[0] and (dx, dy) < best[1]):
            best = (pri2, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]