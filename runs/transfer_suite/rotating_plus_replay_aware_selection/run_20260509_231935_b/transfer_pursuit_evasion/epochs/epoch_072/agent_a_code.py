def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    # If roles ambiguous, infer from environment name
    if not self_role:
        i_am_pursuer = ("pursuit" in (observation.get("environment_name") or "").lower())

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(x, y, x2, y2):
        dx, dy = x - x2, y - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        val = dist if not i_am_pursuer else -dist

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if val > best_val:
                best, best_val = (dx, dy), val
            # deterministic tie-break: earlier move in moves list
            elif val == best_val:
                for mdx, mdy in moves:
                    if (mdx, mdy) == (dx, dy):
                        best_idx = moves.index((dx, dy))
                        cur_idx = moves.index(best)
                        if best_idx < cur_idx:
                            best = (dx, dy)
                        break

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]