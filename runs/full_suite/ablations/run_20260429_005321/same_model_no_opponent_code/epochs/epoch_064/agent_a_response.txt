def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obs.add((p["x"], p["y"]))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((p[0], p[1]))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            resources.append((p["x"], p["y"]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if resources:
            val = 0
            # Prefer moves that improve capture chances vs opponent
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Higher when we are closer than opponent; also move toward nearest
                val += (opd - myd) * 10 - myd
            # Slightly discourage moving away from opponent too much when resources are scarce
            val += cheb(nx, ny, ox, oy) // 4
        else:
            # No visible resources: head toward opponent corner to contest territory
            val = -cheb(nx, ny, ox, oy)

        # Deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]