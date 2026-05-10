def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    resources = [p for p in resources if p not in obstacles]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # If no visible resources, hold position.
    if not resources:
        return [0, 0]

    # Choose a "best" target resource based on who can reach it first (deny opponent).
    # Higher is better: opponent_farther - self_farther; also bias toward closer targets.
    best_t = None
    best_tv = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        tv = (do - ds, -ds)  # maximize (do-ds), then minimize ds
        if best_tv is None or tv > best_tv:
            best_tv = tv
            best_t = (tx, ty)
    tx, ty = best_t

    # One-step lookahead: evaluate all legal deltas.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_self = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)

        # If we step onto any resource, strongly prefer it (capture priority).
        on_res = 1 if (nx, ny) in set(resources) else 0

        # Also consider improvement against opponent for denial: reduce our distance to target and
        # increase chance the opponent remains behind.
        # Small penalty for moving closer to opponent overall (to avoid suicidal "race").
        opp_to_next = md(nx, ny, ox, oy)

        score = (10 * on_res) - (d_self * 2) + (d_opp - d_self) - (opp_to_next * 0.01)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move