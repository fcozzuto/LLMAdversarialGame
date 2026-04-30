def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources or not valid(sx, sy):
        return [0, 0]

    # Target: prioritize resources we can reach first; else pick where we are "closest behind"
    candidates = []
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        candidates.append((d1 < d2, d1 - d2, d1, rx, ry))
    candidates.sort(key=lambda t: (0 if t[0] else 1, t[1], t[2]))
    _, _, _, tx, ty = candidates[0]

    # If opponent is about to grab it, choose a blocking move near the opponent-to-target ray.
    opp_d = cheb(ox, oy, tx, ty)
    my_d = cheb(sx, sy, tx, ty)
    block_mode = (opp_d <= my_d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if block_mode:
            # Move toward a point that would force the opponent to detour: midpoint on their shortest path (cheb).
            mx = (ox + tx) // 2
            my = (oy + ty) // 2
            score = -cheb(nx, ny, mx, my) - 0.3 * cheb(nx, ny, tx, ty) + 0.2 * cheb(nx, ny, ox, oy)
        else:
            # Move to minimize our distance to target, and slightly increase distance from opponent (discourage sharing).
            score = -cheb(nx, ny, tx, ty) + 0.15 * cheb(nx, ny, ox, oy)

        # Strongly prefer immediate capture if on target
        if nx == tx and ny == ty:
            score += 1000

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]