def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    self_t = set(tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    cx, cy = w // 2, h // 2
    # For center-claiming opponent: expand on our side and try to deny center approach paths.
    # Target band depends on where we are relative to center.
    signx = -1 if sx <= cx else 1
    signy = -1 if sy <= cy else 1
    target = (cx + signx * (w // 4), cy + signy * (h // 4))
    tx, ty = max(0, min(w - 1, target[0])), max(0, min(h - 1, target[1]))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def closeness(x, y):
        return abs(x - tx) + abs(y - ty)

    best = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Base: move closer to our target expansion front.
        sc = -closeness(nx, ny)

        # Immediate territory value.
        if (nx, ny) in unclaimed:
            sc += 5.0
        if (nx, ny) in self_t:
            sc += 1.2
        if (nx, ny) in opp_t:
            sc += 3.5  # flipping bonus on entry

        # Deny opponent: avoid stepping toward them unless it flips.
        d_opp = abs(nx - ox) + abs(ny - oy)
        sc += 0.25 * d_opp
        if (nx, ny) in opp_t:
            sc += 0.8  # encourage contested capture

        # Keep away from center if we're already ahead near it; otherwise allow some progress.
        d_center = abs(nx - cx) + abs(ny - cy)
        sc += -0.15 * d_center if (sx <= cx and sy <= cy) or (sx >= cx and sy >= cy) else 0.05 * (-d_center)

        # Tie-break deterministically toward smaller dx, then dy, then direction-free preference.
        if sc > best_score or (sc == best_score and (dx, dy) < best):
            best_score = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]