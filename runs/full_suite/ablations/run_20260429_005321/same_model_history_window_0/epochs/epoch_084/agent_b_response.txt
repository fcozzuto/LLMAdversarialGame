def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(x), int(y)) for x, y in obstacles}
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    dist = lambda a, b, c, d: max(abs(a - c), abs(b - d))  # Chebyshev (diagonal moves)
    steps = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    steps.sort(key=lambda t: -(t == (0, 0)))  # deterministic tie-break; prefer not-stay
    if resources:
        best = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            if (rx, ry) in obs_set:
                continue
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources where we're closer; also prefer fewer remaining resources indirectly via od-sd
            score = (od - sd, -sd)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        if best is not None:
            _, tx, ty = best
            best_move, best_val = (0, 0), (-10**9, -10**9)
            for dx, dy in steps:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obs_set:
                    continue
                ns = dist(nx, ny, tx, ty)
                # Value: improve relative position vs opponent for the same target
                vo = dist(ox, oy, tx, ty)
                val = (vo - ns, -ns)
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
            return [int(best_move[0]), int(best_move[1])]
    # No resources or none valid: move toward center while keeping away from opponent if possible
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_val(nx, ny):
        return -max(abs(nx - cx), abs(ny - cy))
    best_move, best_val = (0, 0), (-10**9, -10**9)
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        # Prefer closer to center; if tie, prefer being farther from opponent
        val = (center_val(nx, ny), max(abs(nx - ox), abs(ny - oy)))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]