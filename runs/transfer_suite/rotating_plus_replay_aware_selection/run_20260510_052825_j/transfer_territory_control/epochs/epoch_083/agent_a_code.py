def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(tuple(o) for o in (observation.get("obstacles") or []) if len(o) >= 2)
    scores = observation.get("scores") or {}
    my_score = scores.get("self", observation.get("self_score", 0)) if isinstance(scores, dict) else observation.get("self_score", 0)
    op_score = scores.get("opponent", observation.get("opponent_score", 0)) if isinstance(scores, dict) else observation.get("opponent_score", 0)
    ahead = my_score >= op_score

    res = observation.get("resources") or []
    resources = [tuple(r) for r in res if len(r) >= 2]
    target = None
    if not ahead and resources:
        target = sorted(resources)[0]
    if ahead and resources:
        target = sorted(resources)[-1]
    if target is None:
        target = (px, py)

    tx, ty = target
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    best_val = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = abs(tx - nx) + abs(ty - ny)
        d_to_opp = abs(px - nx) + abs(py - ny)
        val = 0
        if ahead:
            val = -d_to_target + 0.2 * d_to_opp
        else:
            val = -d_to_opp + 0.2 * (-d_to_target)
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]