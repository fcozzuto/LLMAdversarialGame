def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    vx, vy = sign(ox - sx), sign(oy - sy)
    cand_opp = []
    for odx, ody in deltas:
        nox, noy = ox + odx, oy + ody
        if inb(nox, noy):
            dist = (nox - sx) * (nox - sx) + (noy - sy) * (noy - sy)
            pref = odx * vx + ody * vy
            cand_opp.append((dist, pref, odx, ody, nox, noy))

    if cand_opp:
        # opponent prediction: prefer maximizing distance; break ties by moving most "away" from us
        cand_opp.sort(key=lambda t: (-t[0], -t[1], t[2], t[3]))
        _, _, _, _, px, py = cand_opp[0]
    else:
        px, py = ox, oy

    # choose our move to minimize distance to predicted opponent next
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d2 = (nx - px) * (nx - px) + (ny - py) * (ny - py)
        # slight tie-breaker to keep pressure: prefer smaller distance to current opponent as well
        dcur = abs(nx - ox) + abs(ny - oy)
        score = (d2, dcur, abs(dx) + abs(dy))
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]