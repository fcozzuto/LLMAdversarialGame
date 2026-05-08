def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", [])
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    opp_pos = (ox, oy)
    unclaimed_list = [tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]
    targets = unclaimed_list if unclaimed_list else [opp_pos]

    best_key = None
    best_move = [0, 0]

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in blocked:
                continue

            if targets:
                md = None
                for t in targets:
                    d = dist2((nx, ny), t)
                    if md is None or d < md:
                        md = d
            else:
                md = 0

            steal = 1 if (nx, ny) in opp_terr else 0
            # Prefer: close to unclaimed, then steal if beneficial, then move away from being stuck near opponent.
            # Also lightly prefer progress toward center-ish by using opponent distance as a proxy (deterministic).
            d_opp = dist2((nx, ny), opp_pos)
            key = (md, -steal, d_opp, ny, nx, dx, dy)

            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return best_move