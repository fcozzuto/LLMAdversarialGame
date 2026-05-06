def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                # base: prefer getting closer to contested resources
                best_for_cell = None
                for r in resources:
                    if not (isinstance(r, (list, tuple)) and len(r) == 2):
                        continue
                    rx, ry = r[0], r[1]
                    if not (isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h):
                        continue
                    if (rx, ry) in obs:
                        continue
                    ds = md(nx, ny, rx, ry)
                    do = md(ox, oy, rx, ry)
                    # Want ds small and ds-do small (i.e., be closer than opponent)
                    # Also add slight preference for cells closer to the eventual resource.
                    val = (ds - do, ds)
                    if best_for_cell is None or val < best_for_cell:
                        best_for_cell = val
                # If no resources, fall back to minimizing opponent distance while staying safe
                if best_for_cell is None:
                    sc1 = md(nx, ny, ox, oy)
                    sc2 = md(nx, ny, sx, sy)
                    key = (sc1, sc2, nx, ny)
                else:
                    key = (best_for_cell[0], best_for_cell[1], md(nx, ny, sx, sy), nx, ny)
                cand.append((key, dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    cand.sort()
    return [cand[0][1], cand[0][2]]