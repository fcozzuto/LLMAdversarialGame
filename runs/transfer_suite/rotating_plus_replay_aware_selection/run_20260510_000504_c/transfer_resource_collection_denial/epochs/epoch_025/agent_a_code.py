def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target that we can plausibly reach first; deterministically break ties by coordinates.
    best_cell = None
    best_key = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # Prefer cells where we have advantage; otherwise pursue the best "catch-up" opportunity.
        key = (do - ds, -ds, -((tx << 3) + ty))
        if best_key is None or key > best_key:
            best_key, best_cell = key, (tx, ty)

    tx, ty = best_cell

    # Evaluate next move by resulting position advantage toward target, with mild wall/obstacle safety.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Also consider if there exists a closer alternate resource from nx where we could win sooner.
        alt_bonus = 0
        for ax, ay in resources:
            dsx = md(nx, ny, ax, ay)
            dax = md(ox, oy, ax, ay)
            if dax - dsx > alt_bonus:
                alt_bonus = dax - dsx
        # Score: maximize winning margin; then minimize distance; then keep within grid (implicitly).
        score = (do2 - ds2 + 0.3 * alt_bonus, -ds2, -((nx << 3) + ny))
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]