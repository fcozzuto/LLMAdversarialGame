def choose_move(observation):
    gw, gh = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best = None  # (score, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < gw and 0 <= ny < gh):
                continue
            if (nx, ny) in obstacles:
                continue
            # evaluate by choosing a target resource for this move
            if not resources:
                # no resources: try to move away from opponent
                dist_my = max(abs(nx - ox), abs(ny - oy))
                dist_opp = max(abs(ox - nx), abs(oy - ny))
                sc = dist_my - 0.01 * (abs(dx) + abs(dy)) - 0.01 * dist_opp
                cand = (sc, dx, dy)
            else:
                # target: maximize advantage vs opponent reaching it
                chosen = None
                for rx, ry in resources:
                    myd = max(abs(nx - rx), abs(ny - ry))
                    opd = max(abs(ox - rx), abs(oy - ry))
                    # prefer resources we get earlier and opponent gets later; small tie-bias to closeness
                    adv = (opd - myd)
                    tie = -0.01 * myd
                    val = (adv + tie)
                    if chosen is None or val > chosen[0]:
                        chosen = (val, rx, ry, myd, opd)
                _, rx, ry, myd, opd = chosen
                # additional shaping: move reduces my distance to chosen resource, and keeps away from opponent
                sc = (opd - myd) + 0.05 * (1.0 if myd == 0 else 0.0) + 0.02 * (max(abs(nx - ox), abs(ny - oy)))
                # deterministic micro-preference: straight moves over staying, and small lexicographic
                sc -= 0.001 * (0 if dx == 0 else 1) - 0.0001 * (0 if dy == 0 else 1)
                cand = (sc, dx, dy)
            if best is None or cand > best:
                best = cand

    return [best[1], best[2]] if best is not None else [0, 0]