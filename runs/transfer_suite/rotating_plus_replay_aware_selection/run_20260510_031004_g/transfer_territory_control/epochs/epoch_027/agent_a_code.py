def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - px) + abs(t[1] - py)))
    else:
        # fallback: press toward opponent boundary or along own frontier
        if opp_terr:
            tx, ty = min(opp_terr, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - px) + abs(t[1] - py)))
        else:
            tx, ty = (sx, sy)

    # If close to opponent, try to flip a neighbor they control; otherwise, claim unclaimed.
    near_opp = max(abs(sx - px), abs(sy - py)) <= 2

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        d_t = abs(nx - tx) + abs(ny - ty)
        val += -6 * d_t

        if (nx, ny) in unclaimed:
            val += 320
        if (nx, ny) in self_terr:
            val += 18
        if (nx, ny) in opp_terr:
            val += 120  # flipping on entry

        # Prefer moving closer to opponent when near_opp, to enable flips/counterclaim.
        d_p = abs(nx - px) + abs(ny - py)
        val += (-3 * d_p) if near_opp else (-1 * d_p)

        # Avoid stepping into areas where opponent is strictly closer (territory-control contest).
        # (Using Chebyshev-like distance since diagonal moves are allowed.)
        if opp_terr or unclaimed:
            myd = max(abs(nx - px), abs(ny - py))
            if myd == 0:
                val -= 20
            val += 14 if myd > 1 else -8

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then (0,0).
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]